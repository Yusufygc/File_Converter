import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// `IOptionsProvider.option_specs`'teki tek bir `OptionSpec`'i çizer.
// `spec.kind` → text | password | choice | int. Yeni bir tür
// core/interfaces/option_schema_interface.py'ye eklenirse burası da güncellenir.
RowLayout {
    id: root

    property var spec: ({})
    property bool fieldEnabled: true

    signal valueEdited(string key, var value)

    spacing: 8

    function choiceIndexOf(value) {
        var list = spec.choices || []
        for (var i = 0; i < list.length; i++) {
            if (list[i].value === value) return i
        }
        return 0
    }

    Text {
        text: (spec.label || "") + (spec.required ? " *" : "") + ":"
        font.family: theme.fontFamily
        font.pointSize: 9.5
        color: theme.textSecondary
    }

    ModernTextField {
        visible: spec.kind === "text" || spec.kind === "password"
        Layout.preferredWidth: 180
        enabled: root.fieldEnabled
        placeholderText: spec.placeholder || ""
        echoMode: spec.kind === "password" ? TextInput.Password : TextInput.Normal
        text: (spec.kind === "text" && spec.default !== null && spec.default !== undefined) ? String(spec.default) : ""
        onTextEdited: root.valueEdited(spec.key, text)
    }

    ModernComboBox {
        visible: spec.kind === "choice"
        Layout.preferredWidth: 170
        enabled: root.fieldEnabled
        model: spec.choices || []
        textRoleKey: "label"
        currentIndex: root.choiceIndexOf(spec.default)
        onActivated: function(index) {
            root.valueEdited(spec.key, spec.choices[index].value)
        }
    }

    ModernSpinBox {
        visible: spec.kind === "int"
        enabled: root.fieldEnabled
        editable: true
        from: (spec.minimum !== null && spec.minimum !== undefined) ? spec.minimum : 0
        to: (spec.maximum !== null && spec.maximum !== undefined) ? spec.maximum : 9999
        // Görünmez olsa da diğer türlerde de örneklenir; metin varsayılanı int'e atanamaz.
        value: (spec.kind === "int" && typeof spec.default === "number") ? spec.default : 0
        onValueModified: root.valueEdited(spec.key, value)
    }
}
